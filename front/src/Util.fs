module Util

let inline (^) f x = f x

let inline cmdExec (f: unit -> 'T) =
    Elmish.Cmd.OfFunc.attempt (f >> ignore) () raise
