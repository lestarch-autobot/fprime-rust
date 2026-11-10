// ======================================================================
// \title  ActiveFixTester.hpp
// \author ubuntu
// \brief  hpp file for ActiveFix component test harness implementation class
// ======================================================================

#ifndef Fix_ActiveFixTester_HPP
#define Fix_ActiveFixTester_HPP

#include "Fixtures/ActiveFix/ActiveFix.hpp"
#include "Fixtures/ActiveFix/ActiveFixGTestBase.hpp"

namespace Fix {

class ActiveFixTester final : public ActiveFixGTestBase {

public:
  // ----------------------------------------------------------------------
  // Constants
  // ----------------------------------------------------------------------

  // Maximum size of histories storing events, telemetry, and port outputs
  static const FwSizeType MAX_HISTORY_SIZE = 10;

  // Instance ID supplied to the component instance under test
  static const FwEnumStoreType TEST_INSTANCE_ID = 0;

  // Queue depth supplied to the component instance under test
  static const FwSizeType TEST_INSTANCE_QUEUE_DEPTH = 10;

public:
  // ----------------------------------------------------------------------
  // Construction and destruction
  // ----------------------------------------------------------------------

  //! Construct object ActiveFixTester
  ActiveFixTester();

  //! Destroy object ActiveFixTester
  ~ActiveFixTester();

public:
  // ----------------------------------------------------------------------
  // Tests
  // ----------------------------------------------------------------------

  //! To do
  void UT_SHIM_5_activeDispatchesPortAndCommand();

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
  ActiveFix component;
};

} // namespace Fix

#endif
