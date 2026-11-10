module Fix {
  @ PassiveFix shim fixture: UT-SHIM-1/2/3/4/5/7/8/10
  @ fprime-rust
  passive component PassiveFix {
    sync input port sIn: Val
    guarded input port gIn: Val
    sync input port strIn: Str
    sync input port slowIn: Plain
    output port vOut: Val
    output port sOut: Str
    command recv port cmdIn
    command reg port cmdRegOut
    command resp port cmdResponseOut
    event port eventOut
    text event port textEventOut
    time get port timeGetOut
    telemetry port tlmOut
    param get port prmGetOut
    param set port prmSetOut

    @ OK when m is ON, VALIDATION_ERROR otherwise
    sync command SC(m: Mode)
    @ logs E_S200(s)
    guarded command GC(s: string)
    @ 1: a 48-byte string into E_S40 and T_STR; 2: "ab\0cd" into E_S40
    sync command EMIT(kind: U32)
    @ one event per non-fatal severity, each with x
    sync command LOG_ALL(x: U32)
    sync command FATAL_NOW(x: U32)
    @ every telemetry type row derived from x
    sync command TLM_ALL(x: U32)
    @ reads P_U32 / P_NODEF into T_PRM, T_VALID / T_PRM2, T_VALID2
    sync command PRM
    @ panics in Rust when `really` is set; otherwise responds OK (covers the handler without aborting)
    sync command PANIC(really: bool)

    telemetry T_U32: U32
    telemetry T_I8: I8
    telemetry T_F64: F64
    telemetry T_BOOL: bool
    telemetry T_STR: string size 40
    telemetry T_MODE: Mode
    telemetry T_PRM: U32
    telemetry T_VALID: U32
    telemetry T_PRM2: U32
    telemetry T_VALID2: U32

    param P_U32: U32 default 3
    param P_NODEF: U32

    event E_ALO(x: U32) severity activity low format "{}"
    event E_AHI(x: U32) severity activity high format "{}"
    event E_WLO(x: U32) severity warning low format "{}"
    event E_WHI(x: U32) severity warning high format "{}"
    event E_CMD(x: U32) severity command format "{}"
    event E_DIAG(x: U32) severity diagnostic format "{}"
    event E_FATAL(x: U32) severity fatal format "{}"
    event E_S40(s: string size 40) severity activity low format "{}"
    event E_S200(s: string) severity activity low format "{}"
  }
}
