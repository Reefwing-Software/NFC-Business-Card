// SPDX-License-Identifier: MIT
// Host tests of the same provisioning logic compiled into the Arduino sketch.
#include "../ReefwingWriteURL/ProvisionURL.h"
#include <cassert>
#include <iostream>
#include <string>
#include <vector>
using namespace ReefwingURL;
struct FakeTag {
  uint8_t memory[0x39][16] = {};
  uint8_t status = 0, config = 0;
  bool failRead = false, corrupt = false;
  int failWrite = -1;
  std::vector<unsigned> writes;
  FakeTag() { memory[0][0] = 4; memory[0x38][15] = 255; }
  bool session(uint8_t reg, uint8_t &value) {
    value = reg == 6 ? status : config;
    return !failRead;
  }
  bool read(uint8_t block, uint8_t *data) {
    memcpy(data, memory[block], 16); return !failRead;
  }
  bool write(uint8_t block, const uint8_t *data) {
    writes.push_back(block);
    if (int(writes.size()) == failWrite) return false;
    if (block == 0) {
      assert(data[0] == 0xAA); // Preserve the 7-bit 55 address.
      assert(data[10] == 0 && data[11] == 0);
    }
    memcpy(memory[block], data, 16);
    if (block == 0) memory[0][0] = 4;
    if (corrupt) memory[block][5] ^= 1;
    return true;
  }
};
int main() {
  // Independently decode the NDEF header and URI length/prefix/terminator.
  assert(MESSAGE[0] == 3 && MESSAGE[1] == 21 && MESSAGE[2] == 0xD1);
  assert(MESSAGE[3] == 1 && MESSAGE[4] == 17 && MESSAGE[5] == 'U');
  assert(MESSAGE[6] == 2 && MESSAGE[23] == 0xFE);
  assert("https://www." + std::string(reinterpret_cast<const char *>(MESSAGE+7), 16)
         == "https://www.reefwing.com.au/");
  FakeTag fresh;
  fresh.memory[0][3] = 0x91; // Preserve UID bytes.
  assert(provision(fresh) == OK);
  assert((fresh.writes == std::vector<unsigned>{1,2,1,0}));
  assert(fresh.memory[0][3] == 0x91);
  assert(!memcmp(fresh.memory[0]+12, CC, 4));
  assert(!memcmp(fresh.memory[1], MESSAGE, 32));
  fresh.writes.clear();
  assert(provision(fresh) == OK && fresh.writes.empty());
  for (uint8_t status : {1,2,4,32}) {
    FakeTag tag; tag.status = status;
    assert(provision(tag) == FIELD_OR_BUSY && tag.writes.empty());
  }
  for (int mode = 0; mode < 5; ++mode) {
    FakeTag tag;
    if (mode == 0) tag.memory[0][10] = 1;
    if (mode == 1) tag.memory[0x38][15] = 4;
    if (mode == 2) tag.memory[0][12] = 0xFF;
    if (mode == 3) tag.config = 0x40;
    if (mode == 4) tag.config = 2;
    assert(provision(tag) == PROTECTED_OR_CONFIG && tag.writes.empty());
  }
  FakeTag missing; missing.failRead = true;
  assert(provision(missing) == BUS && missing.writes.empty());
  FakeTag corrupt; corrupt.corrupt = true;
  assert(provision(corrupt) == VERIFY && corrupt.writes.size() == 1);
  FakeTag failed; failed.failWrite = 2;
  assert(provision(failed) == BUS && failed.writes.size() == 2);
  assert(failed.memory[1][1] == 0); // Failed tail never publishes new length.
  assert(failed.memory[0][12] == 0); // Failed write never publishes fresh CC.
  std::cout << "All URL provisioning tests passed\n";
}
