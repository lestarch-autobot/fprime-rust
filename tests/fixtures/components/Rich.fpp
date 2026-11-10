module Fx {
  enum Mode : U8 { OFF, ON }
  type Count = U32
  port Val(a: U32, ref s: string size 20, m: Mode) -> Count
  port Str(s: string)
  @ fprime-rust
  queued component Rich {
    sync input port vIn: Val
    guarded input port gIn: Val
    async input port aIn: Str hook
    output port vOut: Val
    output port sOut: Str
    internal port ip(x: U32, s: string) hook
    sync input port run: Svc.Sched
    command recv port cmdIn
    command reg port cmdRegOut
    command resp port cmdResponseOut
    event port eventOut
    text event port textEventOut
    time get port timeGetOut
    telemetry port tlmOut
    param get port prmGetOut
    param set port prmSetOut
    async command AC(s: string, n: Count) hook
    sync command SC(m: Mode)
    guarded command GC
    telemetry T1: F64
    telemetry T2: string size 40
    telemetry T3: Mode
    param P1: U32 default 3
    param P2: string size 12 default "x"
    event E1(b: bool, s: string size 40) severity warning low format "{} {}"
    event E2(m: Mode) severity fatal format "{}"
  }
}
