1. The input is processed into a series of tokens using regular expressions.
   * Calculator#_tokenize
2. The tokens are turned into a tree of RuleMatches using a right-recursive pattern matching algorithm.
   * Calculator#_match
3. The tree is fixed. Unnecessary tokens are removed, precedence issues are fixed, etc.
   * Ast#_fixed
4. The tree is evaluated in a recursive fashion.
   * Ast#evaluate