// ======================================================================
// \title  QueuedFixTester.hpp
// \author ubuntu
// \brief  hpp file for QueuedFix component test harness implementation class
// ======================================================================

#ifndef Fix_QueuedFixTester_HPP
#define Fix_QueuedFixTester_HPP

#include "Fixtures/QueuedFix/QueuedFix.hpp"
#include "Fixtures/QueuedFix/QueuedFixGTestBase.hpp"

namespace Fix {

class QueuedFixTester final : public QueuedFixGTestBase {

public:
  // ----------------------------------------------------------------------
  // Constants
  // ----------------------------------------------------------------------

  // Maximum size of histories storing events, telemetry, and port outputs
  static const FwSizeType MAX_HISTORY_SIZE = 10;

  // Instance ID supplied to the component instance under test
  static const FwEnumStoreType TEST_INSTANCE_ID = 0;

  // Queue depth supplied to the component instance under test
  static const FwSizeType TEST_INSTANCE_QUEUE_DEPTH = 2;

public:
  // ----------------------------------------------------------------------
  // Construction and destruction
  // ----------------------------------------------------------------------

  //! Construct object QueuedFixTester
  QueuedFixTester();

  //! Destroy object QueuedFixTester
  ~QueuedFixTester();

public:
  // ----------------------------------------------------------------------
  // Tests
  // ----------------------------------------------------------------------

  //! To do
  void UT_SHIM_6_runDrainsQueueOnceOnCallerThread();
  void UT_SHIM_9_internalPortAndOverflowHooks();
  void UT_SHIM_3_queuedSyncCallersAreSerialized();

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
  QueuedFix component;
};

} // namespace Fix

#endif
