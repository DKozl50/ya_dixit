module Init

open Elmish
open Model
open Util

let initPage =
    Browser.Dom.document.getElementById("initial-page").innerHTML
    |> Thoth.Json.Decode.Auto.fromString<Page>
    |> resultCollapse Page.Lobby

let initCmd =
    Browser.Dom.document.getElementById("initial-message").innerHTML
    |> Thoth.Json.Decode.Auto.fromString<Msg>
    |> resultMap Cmd.ofMsg
    |> resultCollapse Cmd.none

let setDispatch: Cmd<Msg> =
    [ fun dispatch -> globalDispatch <- dispatch ]

let initModel =
    { Page = initPage
      Storage = Storage.loadStorage () }

let sendInfo =
    Cmd.ofMsg
    ^ Msg.UserMsg
    ^ UserMessage.UpdateInfo initModel.Storage

let init () =
    initModel, Cmd.batch [ initCmd; setDispatch; sendInfo ]
