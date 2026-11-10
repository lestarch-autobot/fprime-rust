#include <string>
#include <thread>
// ======================================================================
// \title  PassiveFixTester.cpp
// \author ubuntu
// \brief  cpp file for PassiveFix component test harness implementation class
// ======================================================================

#include "PassiveFixTester.hpp"

namespace Fix {

// ----------------------------------------------------------------------
// Construction and destruction
// ----------------------------------------------------------------------

PassiveFixTester::PassiveFixTester()
    : PassiveFixGTestBase("PassiveFixTester", PassiveFixTester::MAX_HISTORY_SIZE),
      component("PassiveFix") {
  this->initComponents();
  this->connectPorts();
}

PassiveFixTester::~PassiveFixTester() { this->component.deinit(); }

extern "C" {
U32 fix_passive_count(U32 index);
void fix_passive_reset();
FwSizeType fix_passive_trace(U32* out, FwSizeType capacity);
}

// ----------------------------------------------------------------------
// Handlers for typed from ports
// ----------------------------------------------------------------------

U32 PassiveFixTester::from_vOut_handler(FwIndexType portNum, U32 a, Fw::StringBase& s, const Fix::Mode& m) {
    this->pushFromPortEntry_vOut(a, s, m);
    return 100;
}

// ----------------------------------------------------------------------
// Tests
// ----------------------------------------------------------------------

void PassiveFixTester::UT_SHIM_1_syncAndGuardedCommands() {
    this->sendCmd_SC(0, 1, Fix::Mode::ON);
    ASSERT_CMD_RESPONSE(0, PassiveFix::OPCODE_SC, 1, Fw::CmdResponse::OK);
    this->sendCmd_SC(0, 2, Fix::Mode::OFF);
    ASSERT_CMD_RESPONSE(1, PassiveFix::OPCODE_SC, 2, Fw::CmdResponse::VALIDATION_ERROR);
    this->sendCmd_GC(0, 3, Fw::CmdStringArg("hi"));
    ASSERT_CMD_RESPONSE(2, PassiveFix::OPCODE_GC, 3, Fw::CmdResponse::OK);
    ASSERT_EVENTS_E_S200_SIZE(1);
    ASSERT_EVENTS_E_S200(0, "hi");
}

void PassiveFixTester::UT_SHIM_2_typedPortsReturnValuesAndOutputPorts() {
    Fw::String s("abc");
    ASSERT_EQ(this->invoke_to_sIn(0, 5, s, Fix::Mode::ON), 101u);
    ASSERT_from_vOut_SIZE(1);
    ASSERT_from_vOut(0, 5u, Fw::String("abc"), Fix::Mode(Fix::Mode::ON));
    ASSERT_TLM_T_STR(0, "abc");
    ASSERT_EQ(this->invoke_to_gIn(0, 3, s, Fix::Mode::ON), 3u * 2u + 1u + 3u);
    this->invoke_to_strIn(0, Fw::String("xyz"));
    ASSERT_from_sOut_SIZE(1);
    ASSERT_from_sOut(0, Fw::String("xyz"));
}

void PassiveFixTester::UT_SHIM_3_passiveSyncCallersAreSerialized() {
    fix_passive_reset();
    std::thread first([this]() { this->invoke_to_slowIn(0, 1); });
    std::thread second([this]() { this->invoke_to_slowIn(0, 2); });
    first.join();
    second.join();
    U32 trace[8] = {0};
    ASSERT_EQ(fix_passive_trace(trace, 8), 4u);
    const bool firstThenSecond = trace[0] == 10 && trace[1] == 11 && trace[2] == 20 && trace[3] == 21;
    const bool secondThenFirst = trace[0] == 20 && trace[1] == 21 && trace[2] == 10 && trace[3] == 11;
    ASSERT_TRUE(firstThenSecond || secondThenFirst) << trace[0] << trace[1] << trace[2] << trace[3];
}

void PassiveFixTester::UT_SHIM_4_lifecycleAndParameterUpdated() {
    fix_passive_reset();
    {
        PassiveFix scoped("scoped");
        ASSERT_EQ(fix_passive_count(0), 1u);
        ASSERT_EQ(fix_passive_count(1), 0u);
        scoped.init(0);
        ASSERT_EQ(fix_passive_count(1), 1u);
        ASSERT_EQ(fix_passive_count(2), 0u);
    }
    ASSERT_EQ(fix_passive_count(0), 1u);
    ASSERT_EQ(fix_passive_count(1), 1u);
    ASSERT_EQ(fix_passive_count(2), 1u);
    ASSERT_EQ(fix_passive_count(3), 0u);
    this->paramSet_P_U32(7, Fw::ParamValid::VALID);
    this->paramSend_P_U32(0, 9);
    ASSERT_EQ(fix_passive_count(3), 1u);
    ASSERT_CMD_RESPONSE(0, PassiveFix::OPCODE_P_U32_SET, 9, Fw::CmdResponse::OK);
}

void PassiveFixTester::UT_SHIM_7_oneEventPerSeverity() {
    this->sendCmd_LOG_ALL(0, 1, 7);
    ASSERT_EVENTS_SIZE(6);
    ASSERT_EVENTS_E_ALO(0, 7);
    ASSERT_EVENTS_E_AHI(0, 7);
    ASSERT_EVENTS_E_WLO(0, 7);
    ASSERT_EVENTS_E_WHI(0, 7);
    ASSERT_EVENTS_E_CMD(0, 7);
    ASSERT_EVENTS_E_DIAG(0, 7);
    this->sendCmd_FATAL_NOW(0, 2, 9);
    ASSERT_EVENTS_E_FATAL_SIZE(1);
    ASSERT_EVENTS_E_FATAL(0, 9);
}

void PassiveFixTester::UT_SHIM_8_telemetryRowsAndParamGet() {
    this->sendCmd_TLM_ALL(0, 1, 5);
    ASSERT_TLM_T_U32(0, 5);
    ASSERT_TLM_T_I8(0, -5);
    ASSERT_TLM_T_F64(0, 2.5);
    ASSERT_TLM_T_BOOL(0, true);
    ASSERT_TLM_T_MODE(0, Fix::Mode::ON);
    // (value, VALID) and (value, INVALID)
    this->paramSet_P_U32(9, Fw::ParamValid::VALID);
    this->paramSet_P_NODEF(0, Fw::ParamValid::INVALID);
    this->component.loadParameters();
    this->sendCmd_PRM(0, 2);
    ASSERT_TLM_T_PRM(0, 9);
    ASSERT_TLM_T_VALID(0, static_cast<U32>(Fw::ParamValid::VALID));
    ASSERT_TLM_T_VALID2(0, static_cast<U32>(Fw::ParamValid::INVALID));
    // (default, DEFAULT)
    this->paramSet_P_U32(0, Fw::ParamValid::INVALID);
    this->component.loadParameters();
    this->sendCmd_PRM(0, 3);
    ASSERT_TLM_T_PRM(1, 3);
    ASSERT_TLM_T_VALID(1, static_cast<U32>(Fw::ParamValid::DEFAULT));
}

void PassiveFixTester::UT_SHIM_10_stringTruncationNulAndInvalidUtf8() {
    const std::string forty(40, 'x');
    this->sendCmd_EMIT(0, 1, 1);
    ASSERT_EVENTS_E_S40_SIZE(1);
    ASSERT_EVENTS_E_S40(0, forty.c_str());
    ASSERT_TLM_T_STR(0, forty.c_str());
    this->sendCmd_EMIT(0, 2, 2);
    ASSERT_EVENTS_E_S40(1, "ab");
    Fw::String invalid("\xFF" "A");
    this->invoke_to_strIn(0, invalid);
    ASSERT_TLM_T_STR(1, "\xEF\xBF\xBD" "A");
}

void PassiveFixTester::panicInHandler() {
    this->sendCmd_PANIC(0, 1);
}

}  // namespace Fix
