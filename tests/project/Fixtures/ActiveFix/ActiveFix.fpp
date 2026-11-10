module Fix {
  @ Active shim fixture: UT-SHIM-3 (active), UT-SHIM-5 (active)
  @ fprime-rust
  active component ActiveFix {
    @ writes T_X(x); x == 777 sleeps 200 ms first (UT-SHIM-3)
    async input port aIn: Plain
    @ writes T_X(x) (UT-SHIM-3: serialized against aIn)
    guarded input port gIn: Plain
    command recv port cmdIn
    command reg port cmdRegOut
    command resp port cmdResponseOut
    event port eventOut
    text event port textEventOut
    time get port timeGetOut
    telemetry port tlmOut

    @ logs E_X(x)
    async command AC(x: U32)

    telemetry T_X: U32
    @ getNumMsgsDropped as seen from Rust (covers the num_msgs_dropped helper)
    telemetry T_DROPPED: U32
    event E_X(x: U32) severity activity low format "{}"
  }
}
