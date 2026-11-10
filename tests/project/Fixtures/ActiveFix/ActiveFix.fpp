module Fix {
  @ Active shim fixture: UT-SHIM-5 (active)
  @ fprime-rust
  active component ActiveFix {
    @ writes T_X(x)
    async input port aIn: Plain
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
    event E_X(x: U32) severity activity low format "{}"
  }
}
