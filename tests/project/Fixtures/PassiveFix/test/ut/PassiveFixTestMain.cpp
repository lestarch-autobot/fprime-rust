// UT-SHIM-1/2/3/4/5/7/8/10 over the passive fixture
#include "Fixtures/PassiveFix/test/ut/PassiveFixTester.hpp"

#define SHIM_TEST(name) TEST(Nominal, name) { Fix::PassiveFixTester().name(); }

SHIM_TEST(UT_SHIM_1_syncAndGuardedCommands)
SHIM_TEST(UT_SHIM_2_typedPortsReturnValuesAndOutputPorts)
SHIM_TEST(UT_SHIM_3_passiveSyncCallersAreSerialized)
SHIM_TEST(UT_SHIM_4_lifecycleAndParameterUpdated)
SHIM_TEST(UT_SHIM_7_oneEventPerSeverity)
SHIM_TEST(UT_SHIM_8_telemetryRowsAndParamGet)
SHIM_TEST(UT_SHIM_10_stringTruncationNulAndInvalidUtf8)

TEST(Nominal, panicDisarmedRespondsOk) { Fix::PassiveFixTester().panicDisarmedRespondsOk(); }

TEST(Death, UT_SHIM_7_panicReachesFprimeAssert) {
    // the panic location (file:line in Rust) reaches FW_ASSERT and the process aborts
    ASSERT_DEATH(Fix::PassiveFixTester().panicInHandler(), "PassiveFix\\.rs:[0-9]+");
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
