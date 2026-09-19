// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Reefwing Software
#pragma once
#include <stdint.h>
#include <string.h>

namespace ReefwingURL {
constexpr uint8_t ADDRESS = 0x55;
// Type 2 TLV; short, well-known URI record; prefix 02 = https://www.
constexpr uint8_t MESSAGE[32] = {
  0x03, 0x15, 0xD1, 0x01, 0x11, 0x55, 0x02,
  'r','e','e','f','w','i','n','g','.','c','o','m','.','a','u','/',
  0xFE // Remaining bytes are zero padding.
};
constexpr uint8_t CC[4] = {0xE1, 0x10, 0x6D, 0x00};
enum Result : uint8_t { OK = 0, BUS = 1, FIELD_OR_BUSY = 2,
                       PROTECTED_OR_CONFIG = 3, VERIFY = 4 };

// Transport provides block reads/writes and session-register reads. Writes
// must wait for EEPROM programming to finish before returning (even on error).
template<class Transport> Result ready(Transport &tag) {
  uint8_t status;
  if (!tag.session(6, status)) return BUS;
  // RF_FIELD_PRESENT, EEPROM_WR_BUSY/ERR, RF_LOCKED. Never write under RF.
  return (status & 0x27) ? FIELD_OR_BUSY : OK;
}

template<class Transport>
Result checkedWrite(Transport &tag, uint8_t block, const uint8_t *data) {
  Result result = ready(tag);
  if (result != OK) return result;
  if (!tag.write(block, data)) return BUS;
  result = ready(tag);
  if (result != OK) return result;
  uint8_t actual[16];
  if (!tag.read(block, actual)) return BUS;
  // Block 0 byte 0 reads the UID manufacturer ID, not the I2C address.
  if (block == 0 && actual[0] != 0x04) return VERIFY;
  const uint8_t start = block == 0 ? 1 : 0;
  return memcmp(actual + start, data + start, 16 - start) ? VERIFY : OK;
}

template<class Transport> Result provision(Transport &tag) {
  Result result = ready(tag);
  if (result != OK) return result;
  uint8_t config;
  if (!tag.session(0, config)) return BUS;
  if (config & 0x42) return PROTECTED_OR_CONFIG; // SRAM mirror/pass-through.
  uint8_t header[16], data[16];
  if (!tag.read(0, header) || !tag.read(0x38, data)) return BUS;
  if (header[0] != 0x04 || header[10] || header[11] || data[15] <= 0xEB)
    return PROTECTED_OR_CONFIG;
  bool blankCC = true;
  for (uint8_t i = 12; i < 16; ++i) blankCC &= header[i] == 0;
  if (!blankCC && memcmp(header + 12, CC, 4)) return PROTECTED_OR_CONFIG;

  bool matches = true;
  for (uint8_t block = 1; block <= 2; ++block) {
    if (!tag.read(block, data)) return BUS;
    if (memcmp(data, MESSAGE + (block - 1) * 16, 16)) matches = false;
  }
  if (!matches) {
    // Invalidate old TLV first; publish the length only after the tail is safe.
    memset(data, 0, sizeof(data));
    data[0] = 0x03;
    data[2] = 0xFE;
    result = checkedWrite(tag, 1, data);
    if (result != OK) return result;
    result = checkedWrite(tag, 2, MESSAGE + 16);
    if (result != OK) return result;
    result = checkedWrite(tag, 1, MESSAGE);
    if (result != OK) return result;
  }
  if (blankCC) {
    memcpy(header + 12, CC, 4);
    // CRITICAL: writing back the read value 04 would change the I2C address!
    header[0] = ADDRESS << 1;
    result = checkedWrite(tag, 0, header);
    if (result != OK) return result;
  }
  return ready(tag);
}
} // namespace ReefwingURL
