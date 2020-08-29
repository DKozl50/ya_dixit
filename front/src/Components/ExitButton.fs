module Components.ExitButton

open Feliz
open Model

let exitButtonComponent =
    React.functionComponent (fun (a: {| Dispatch: Msg -> unit |}) ->
        Html.a [ prop.className "delete is-large"
                 prop.style [ style.position.absolute
                              style.top (length.px 10)
                              style.right (length.px 10) ]
                 prop.onClick (fun _ -> a.Dispatch(Msg.UserMsg(UserMessage.LeaveRoom))) ])
