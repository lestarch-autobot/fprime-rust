// ======================================================================
// \title  PassiveFixTester.hpp
// \author ubuntu
// \brief  hpp file for PassiveFix component test harness implementation class
// ======================================================================

#ifndef Fix_PassiveFixTester_HPP
#define Fix_PassiveFixTester_HPP

#include "Fixtures/PassiveFix/PassiveFix.hpp"
#include "Fixtures/PassiveFix/PassiveFixGTestBase.hpp"

namespace Fix {

class PassiveFixTester final : public PassiveFixGTestBase {

public:
  // ----------------------------------------------------------------------
  // Constants
  // ----------------------------------------------------------------------

  // Maximum size of histories storing events, telemetry, and port outputs
  static const FwSizeType MAX_HISTORY_SIZE = 10;

  // Instance ID supplied to the component instance under test
  static const FwEnumStoreType TEST_INSTANCE_ID = 0;

public:
  // ----------------------------------------------------------------------
  // Construction and destruction
  // ----------------------------------------------------------------------

  //! Construct object PassiveFixTester
  PassiveFixTester();

  //! Destroy object PassiveFixTester
  ~PassiveFixTester();

public:
  // ----------------------------------------------------------------------
  // Tests
  // ----------------------------------------------------------------------

  //! To do
  void UT_SHIM_1_syncAndGuardedCommands();
  void UT_SHIM_2_typedPortsReturnValuesAndOutputPorts();
  void UT_SHIM_3_passiveSyncCallersAreSerialized();
  void UT_SHIM_4_lifecycleAndParameterUpdated();
  void UT_SHIM_7_oneEventPerSeverity();
  void UT_SHIM_8_telemetryRowsAndParamGet();
  void UT_SHIM_10_stringTruncationNulAndInvalidUtf8();
  void panicInHandler();

private:
  //! Returns 100 so the Rust caller's `+ 1` is observable
  U32 from_vOut_handler(FwIndexType portNum, U32 a, const Fw::StringBase& s, const Fix::Mode& m) override;

private:
  // ----------------------------------------------------------------------
  // Helper functions
  // ----------------------------------------------------------------------

  //! Connect ports
  void connectPorts();

  //! Initialize components
  void initComponents();

private:
  // ----------------------------------------------------------------------
  // Member variables
  // ----------------------------------------------------------------------

  //! The component under test
  PassiveFix component;
};

} // namespace Fix

#endif
