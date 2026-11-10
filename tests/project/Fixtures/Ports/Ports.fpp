module Fix {
  enum Mode : U8 { OFF, ON }
  port Val(a: U32, s: string size 20, m: Mode) -> U32
  port Str(s: string)
  port Plain(x: U32)
}
