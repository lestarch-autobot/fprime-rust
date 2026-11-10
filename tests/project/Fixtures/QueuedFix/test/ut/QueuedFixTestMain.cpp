// UT-SHIM-3 (queued), UT-SHIM-6, UT-SHIM-9 over the queued fixture
#include "Fixtures/QueuedFix/test/ut/QueuedFixTester.hpp"

TEST(Nominal, UT_SHIM_6_runDrainsQueueOnceOnCallerThread) {
    Fix::QueuedFixTester().UT_SHIM_6_runDrainsQueueOnceOnCallerThread();
}

TEST(Nominal, UT_SHIM_9_internalPortAndOverflowHooks) {
    Fix::QueuedFixTester().UT_SHIM_9_internalPortAndOverflowHooks();
}

TEST(Nominal, UT_SHIM_3_queuedSyncCallersAreSerialized) {
    Fix::QueuedFixTester().UT_SHIM_3_queuedSyncCallersAreSerialized();
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
