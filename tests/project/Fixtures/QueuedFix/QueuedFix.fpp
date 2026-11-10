module Fix {
  @ Queued shim fixture: UT-SHIM-3 (queued), UT-SHIM-5, UT-SHIM-6, UT-SHIM-9
  @ fprime-rust
  queued component QueuedFix {
    @ trace 100+x; x >= 70 invokes ip three times; x >= 50 invokes ip once; overflow: trace 900+x
    async input port aIn: Plain hook
    @ trace 500+x, sleep, trace 600+x (lock edge)
    sync input port sIn: Plain
    @ drains the messages present at entry, then trace 1000 + last_dispatch code
    sync input port run: Svc.Sched
    @ trace 300+x; overflow: trace 700+x
    internal port ip(x: U32) hook
    command recv port cmdIn
    command reg port cmdRegOut
    command resp port cmdResponseOut
    event port eventOut
    text event port textEventOut
    time get port timeGetOut
    telemetry port tlmOut

    @ trace 200+x; overflow: BUSY
    async command AC(x: U32) hook

    telemetry T_DROPPED: U32
  }
}
