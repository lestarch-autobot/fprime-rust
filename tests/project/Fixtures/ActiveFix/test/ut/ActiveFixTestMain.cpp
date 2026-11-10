// UT-SHIM-5 (active) over the active fixture
#include "Fixtures/ActiveFix/test/ut/ActiveFixTester.hpp"

TEST(Nominal, UT_SHIM_3_guardedCallerSerializedAgainstAsyncHandler) {
    Fix::ActiveFixTester().UT_SHIM_3_guardedCallerSerializedAgainstAsyncHandler();
}

TEST(Nominal, UT_SHIM_5_activeDispatchesPortAndCommand) {
    Fix::ActiveFixTester().UT_SHIM_5_activeDispatchesPortAndCommand();
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
