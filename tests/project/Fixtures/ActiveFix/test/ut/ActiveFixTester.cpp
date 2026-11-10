// ======================================================================
// \title  ActiveFixTester.cpp
// \author ubuntu
// \brief  cpp file for ActiveFix component test harness implementation class
// ======================================================================

#include "ActiveFixTester.hpp"

#include "Os/Task.hpp"
#include "Os/RawTime.hpp"
#include "Fw/Test/UnitTest.hpp"

namespace Fix {

// ----------------------------------------------------------------------
// Construction and destruction
// ----------------------------------------------------------------------

ActiveFixTester ::ActiveFixTester()
    : ActiveFixGTestBase("ActiveFixTester", ActiveFixTester::MAX_HISTORY_SIZE),
      component("ActiveFix") {
  this->initComponents();
  this->connectPorts();
}

ActiveFixTester ::~ActiveFixTester() { this->component.deinit(); }

// ----------------------------------------------------------------------
// Tests
// ----------------------------------------------------------------------

void ActiveFixTester::UT_SHIM_3_guardedCallerSerializedAgainstAsyncHandler() {
    REQUIREMENT("REQ-FprimeRust-023");
    COMMENT("UT-SHIM-3 (active): a guarded call from this thread blocks while the component thread runs an async handler");
    this->clearHistory();
    this->component.start();
    this->invoke_to_aIn(0, 777);  // handler sleeps 200 ms on the component thread, holding the instance mutex
    Os::Task::delay(Fw::TimeInterval(0, 50000));
    Os::RawTime before;
    before.now();
    this->invoke_to_gIn(0, 5);
    Os::RawTime after;
    after.now();
    U32 elapsedUs = 0;
    ASSERT_EQ(after.getDiffUsec(before, elapsedUs), Os::RawTime::OP_OK);
    this->component.exit();
    this->component.join();
    ASSERT_GE(elapsedUs, 100000u);
    ASSERT_TLM_T_X_SIZE(2);
    ASSERT_TLM_T_X(0, 777);
    ASSERT_TLM_T_X(1, 5);
}

void ActiveFixTester::UT_SHIM_5_activeDispatchesPortAndCommand() {
    this->clearHistory();
    this->invoke_to_aIn(0, 11);
    ASSERT_TLM_SIZE(0);  // queued until the active component's thread dispatches
    this->component.doDispatch();
    ASSERT_TLM_T_X_SIZE(1);
    ASSERT_TLM_T_X(0, 11);
    this->sendCmd_AC(0, 3, 12);
    ASSERT_EVENTS_SIZE(0);
    this->component.doDispatch();
    ASSERT_EVENTS_E_X_SIZE(1);
    ASSERT_EVENTS_E_X(0, 12);
    ASSERT_CMD_RESPONSE(0, ActiveFix::OPCODE_AC, 3, Fw::CmdResponse::OK);
}

void ActiveFixTester::numMsgsDroppedReadable() {
    REQUIREMENT("REQ-FprimeRust-006");
    COMMENT("active fixture: a guarded handler publishes getNumMsgsDropped() read through ctx.num_msgs_dropped(); zero before any overflow");
    this->clearHistory();
    this->invoke_to_gIn(0, 9);
    ASSERT_TLM_T_X(0, 9);
    ASSERT_TLM_T_DROPPED_SIZE(1);
    ASSERT_TLM_T_DROPPED(0, 0);
    ASSERT_TLM_T_RESP_SIZE(1);
    ASSERT_TLM_T_RESP(0, Fw::CmdResponse::OK);
}

}  // namespace Fix
