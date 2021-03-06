module Util

type RefT = Feliz.IRefValue<option<Browser.Types.HTMLInputElement>>

let inline (^) f x = f x

let inline cmdExec (f: unit -> 'T) =
    Elmish.Cmd.OfFunc.attempt (f >> ignore) () raise

let mutable globalDispatch: Model.Msg -> unit = ignore

let inline isOk x =
    match x with
    | Ok _ -> true
    | Error _ -> false

let inline resultCollapse errorVal =
    function
    | Ok x -> x
    | Error _ -> errorVal

let inline konst x _ = x

let imgSrc (id: Model.CardID) = "/img/" + id

let aviSrc (avi: string) = "/avi/" + avi
