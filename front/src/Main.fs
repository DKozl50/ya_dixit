module Main

open Fable.Core.JsInterop

importAll "bulma/css/bulma.css"
importAll "../styles/styles.sass"

open Elmish
open Elmish.React
open Elmish.Debug
open Elmish.HMR

Program.mkProgram Init.initModel Update.update Render.render
|> Program.withSubscription Socket.serverMessageSubscription
#if DEBUG
|> Program.withDebugger
#endif
|> Program.withReactSynchronous "feliz-app"
|> Program.run
