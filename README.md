# Calculator
Calculator program created by Logan Davenport

Features:
- Expression parsing
  - Parses +, -, *, /, ^, pi, and e
  - Parses logarithms in the following forms:
    - "ln([expr])", natural logarithm
    - "log([expr])", log base 10
    - "log_\[constant]([expr])", log base a constant
    - "log_([expr])([expr])", log base an arbitrary expression
- Simplification
  - Performs basic simplifcation such as removing 0s from additions e.g. log_(x)(5)+0 ==> log_(x)(5)
  - Simplifies exprA^exprB*exprA^exprC to exprA^(exprB+exprC)
  - Variable substitution e.g. parse("x+5").simplify({"x":parse("2^x")}) ==> "2^x+5"
  - TODO: addition simplification e.g. 2*x+5*x ==> 7*x
- Derivatives
  - Can take the derivative of any expression
  - Syntax derivative = f.der

  