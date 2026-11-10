// ======================================================================
// \title  FprimeRust.cpp
// \brief  fprime-rust C++ runtime implementation
// ======================================================================
#include <FprimeRust/FprimeRust.hpp>

#include <cstdlib>
#include <cstring>

#include <Fw/Logger/Logger.hpp>
#include <Fw/Types/Assert.hpp>

namespace FprimeRust {

FwSizeType copyBytes(CHAR* destination, FwSizeType destinationSize, const CHAR* bytes, FwSizeType length) {
    FW_ASSERT(destination != nullptr);
    FW_ASSERT(destinationSize > 0);
    FwSizeType count = (length < destinationSize - 1) ? length : destinationSize - 1;
    if (bytes == nullptr) {
        count = 0;
    }
    // Stop at an interior NUL: the carrier is a C string
    for (FwSizeType i = 0; i < count; i++) {
        if (bytes[i] == '\0') {
            count = i;
            break;
        }
    }
    if (count > 0) {
        (void)std::memcpy(destination, bytes, static_cast<size_t>(count));
    }
    destination[count] = '\0';
    return count;
}

void assignString(Fw::StringBase& destination, const CHAR* bytes, FwSizeType length) {
    // Copy through a bounded, NUL-terminated local so that the carrier's own assignment stays in charge
    CHAR local[FW_FIXED_LENGTH_STRING_SIZE];
    const FwSizeType capacity = destination.getCapacity();
    const FwSizeType bound = (capacity < sizeof(local)) ? capacity : sizeof(local);
    (void)copyBytes(local, bound, bytes, length);
    destination = local;
}

}  // namespace FprimeRust

extern "C" {

U32 fprime_rust_runtime_marker() {
    return 0x52555354U;  // "RUST"
}

void fprime_rust_assert(const CHAR* file, FwSizeType fileLength, U32 line, const CHAR* msg, FwSizeType msgLength) {
    // Bounded NUL-terminated copies: Rust strings are not NUL-terminated
    CHAR fileBuffer[FW_FIXED_LENGTH_STRING_SIZE];
    CHAR msgBuffer[FW_FIXED_LENGTH_STRING_SIZE];
    const FwSizeType fileCount = (fileLength < sizeof(fileBuffer) - 1) ? fileLength : sizeof(fileBuffer) - 1;
    const FwSizeType msgCount = (msgLength < sizeof(msgBuffer) - 1) ? msgLength : sizeof(msgBuffer) - 1;
    if (file != nullptr && fileCount > 0) {
        (void)std::memcpy(fileBuffer, file, static_cast<size_t>(fileCount));
    }
    fileBuffer[fileCount] = '\0';
    if (msg != nullptr && msgCount > 0) {
        (void)std::memcpy(msgBuffer, msg, static_cast<size_t>(msgCount));
    }
    msgBuffer[msgCount] = '\0';
    Fw::Logger::log("Rust panic at %s:%u: %s\n", fileBuffer, line, msgBuffer);
#if FW_ASSERT_LEVEL == FW_FILEID_ASSERT
    Fw::SwAssert(static_cast<U32>(0), static_cast<FwSizeType>(line));
#else
    Fw::SwAssert(fileBuffer, static_cast<FwSizeType>(line));
#endif
    std::abort();
}

void fprime_rust_string_assign(void* carrier, const CHAR* bytes, FwSizeType length) {
    FW_ASSERT(carrier != nullptr);
    FprimeRust::assignString(*static_cast<Fw::StringBase*>(carrier), bytes, length);
}

}  // extern "C"
