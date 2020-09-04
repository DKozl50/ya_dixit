module Util

type RefT = Feliz.IRefValue<option<Browser.Types.HTMLInputElement>>

let inline (^) f x = f x

let inline cmdExec (f: unit -> 'T) =
    Elmish.Cmd.OfFunc.attempt (f >> ignore) () raise

let mutable globalDispatch: Model.Msg -> unit = ignore

let inline resultCollapse errorVal =
    function
    | Ok x -> x
    | Error _ -> errorVal

let inline resultMap func =
    function
    | Ok x -> Ok ^ func x
    | Error e -> Error e

let inline konst x _ = x

let imgSrc (id: Model.CardID) = "/img/" + id

let aviSrc (avi: string) = "/avi/" + avi

