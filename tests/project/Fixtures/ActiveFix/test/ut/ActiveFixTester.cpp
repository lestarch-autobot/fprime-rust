// ======================================================================
// \title  ActiveFixTester.cpp
// \author ubuntu
// \brief  cpp file for ActiveFix component test harness implementation class
// ======================================================================

#include "ActiveFixTester.hpp"

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

void ActiveFixTester::UT_SHIM_5_activeDispatchesPortAndCommand() {
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

}  // namespace Fix
