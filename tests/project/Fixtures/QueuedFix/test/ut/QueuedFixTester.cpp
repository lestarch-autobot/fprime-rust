#include <thread>
// ======================================================================
// \title  QueuedFixTester.cpp
// \author ubuntu
// \brief  cpp file for QueuedFix component test harness implementation class
// ======================================================================

#include "QueuedFixTester.hpp"

namespace Fix {

// ----------------------------------------------------------------------
// Construction and destruction
// ----------------------------------------------------------------------

QueuedFixTester ::QueuedFixTester()
    : QueuedFixGTestBase("QueuedFixTester", QueuedFixTester::MAX_HISTORY_SIZE),
      component("QueuedFix") {
  this->initComponents();
  this->connectPorts();
}

QueuedFixTester ::~QueuedFixTester() { this->component.deinit(); }

extern "C" {
U64 fix_queued_current_thread();
void fix_queued_reset();
FwSizeType fix_queued_trace(U32* marks, U64* threads, FwSizeType capacity);
}

namespace {
const FwSizeType CAPACITY = 16;

struct Trace {
    U32 marks[CAPACITY];
    U64 threads[CAPACITY];
    FwSizeType size;
};

Trace readTrace() {
    Trace trace = {};
    trace.size = fix_queued_trace(trace.marks, trace.threads, CAPACITY);
    return trace;
}
}  // namespace

// ----------------------------------------------------------------------
// Tests
// ----------------------------------------------------------------------

void QueuedFixTester::UT_SHIM_6_runDrainsQueueOnceOnCallerThread() {
    fix_queued_reset();
    this->invoke_to_aIn(0, 1);
    this->sendCmd_AC(0, 7, 2);
    ASSERT_EQ(readTrace().size, 0u);  // queued, not yet dispatched
    this->invoke_to_run(0, 0);
    const Trace trace = readTrace();
    ASSERT_EQ(trace.size, 3u);
    EXPECT_EQ(trace.marks[0], 101u);
    EXPECT_EQ(trace.marks[1], 202u);
    // run_handler entered after the drain; last_dispatch() is the base status of dispatchAvailableMessages()
    // (MSG_DISPATCH_OK after dispatching the messages present at entry, per the SDD name table)
    EXPECT_EQ(trace.marks[2], 1000u + static_cast<U32>(Fw::QueuedComponentBase::MSG_DISPATCH_OK));
    for (FwSizeType i = 0; i < trace.size; i++) {
        EXPECT_EQ(trace.threads[i], fix_queued_current_thread()) << "entry " << i << " ran off the caller's thread";
    }
    ASSERT_CMD_RESPONSE_SIZE(1);
    ASSERT_CMD_RESPONSE(0, QueuedFix::OPCODE_AC, 7, Fw::CmdResponse::OK);
    ASSERT_TLM_T_DROPPED(0, 0);
    // a second run finds the queue empty: nothing re-dispatched
    this->invoke_to_run(0, 0);
    const Trace again = readTrace();
    ASSERT_EQ(again.size, 4u);
    EXPECT_EQ(again.marks[3], 1000u);
}

void QueuedFixTester::UT_SHIM_9_internalPortAndOverflowHooks() {
    // internal port invoked from a Rust handler reaches the Rust internal handler through the queue: it is queued
    // during the drain and dispatched by the next sync entry (the drain covers the messages present at entry)
    fix_queued_reset();
    this->invoke_to_aIn(0, 60);
    this->invoke_to_run(0, 0);
    Trace trace = readTrace();
    ASSERT_EQ(trace.size, 2u);
    EXPECT_EQ(trace.marks[0], 160u);
    EXPECT_EQ(trace.marks[1], 1000u);
    this->invoke_to_run(0, 0);
    trace = readTrace();
    ASSERT_EQ(trace.size, 4u);
    EXPECT_EQ(trace.marks[2], 360u);
    EXPECT_EQ(trace.marks[3], 1000u);
    // async port and async command hooks on a full queue (depth TEST_INSTANCE_QUEUE_DEPTH == 2)
    fix_queued_reset();
    this->invoke_to_aIn(0, 1);
    this->invoke_to_aIn(0, 2);
    this->invoke_to_aIn(0, 3);
    this->sendCmd_AC(0, 9, 4);
    trace = readTrace();
    ASSERT_EQ(trace.size, 1u);
    EXPECT_EQ(trace.marks[0], 903u);
    ASSERT_CMD_RESPONSE_SIZE(1);
    ASSERT_CMD_RESPONSE(0, QueuedFix::OPCODE_AC, 9, Fw::CmdResponse::BUSY);
    this->invoke_to_run(0, 0);
    trace = readTrace();
    ASSERT_EQ(trace.size, 4u);
    EXPECT_EQ(trace.marks[1], 101u);
    EXPECT_EQ(trace.marks[2], 102u);
    EXPECT_EQ(trace.marks[3], 1000u);
    // internal port with hook invoked from a handler onto a full queue: hook runs inside the handler, no re-lock
    fix_queued_reset();
    this->invoke_to_aIn(0, 70);
    this->invoke_to_run(0, 0);
    trace = readTrace();
    ASSERT_EQ(trace.size, 3u);
    EXPECT_EQ(trace.marks[0], 170u);
    EXPECT_EQ(trace.marks[1], 770u);
    EXPECT_EQ(trace.marks[2], 1000u);
    this->invoke_to_run(0, 0);
    trace = readTrace();
    ASSERT_EQ(trace.size, 6u);
    EXPECT_EQ(trace.marks[3], 370u);
    EXPECT_EQ(trace.marks[4], 370u);
    EXPECT_EQ(trace.marks[5], 1000u);
}

void QueuedFixTester::UT_SHIM_3_queuedSyncCallersAreSerialized() {
    fix_queued_reset();
    std::thread first([this]() { this->invoke_to_sIn(0, 1); });
    std::thread second([this]() { this->invoke_to_sIn(0, 2); });
    first.join();
    second.join();
    const Trace trace = readTrace();
    ASSERT_EQ(trace.size, 4u);
    const U32* m = trace.marks;
    const bool firstThenSecond = m[0] == 501 && m[1] == 601 && m[2] == 502 && m[3] == 602;
    const bool secondThenFirst = m[0] == 502 && m[1] == 602 && m[2] == 501 && m[3] == 601;
    ASSERT_TRUE(firstThenSecond || secondThenFirst) << m[0] << m[1] << m[2] << m[3];
}

}  // namespace Fix
