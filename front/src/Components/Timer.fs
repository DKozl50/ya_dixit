module Components.Timer

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

let private playerAviPlaceholder =
    "https://bulma.io/images/placeholders/128x128.png"

type TimerArgs = { Phase: GamePhase; Player: Player }

let private timerComponent' progress =
    let p' = max progress 360.
    let o = -(188.49 / 360.) * p' + 188.49
    Bulma.levelLeft
        [ Html.figure [ prop.className "image" ++ image.is64x64
                        prop.children [ Html.svg [ prop.style [ style.width (length.px 64)
                                                                style.height (length.px 64)
                                                                style.position.absolute
                                                                style.top 0
                                                                style.transform.rotate -90 ]
                                                   prop.children
                                                       [ Html.circle [ prop.cx 32
                                                                       prop.cy 32
                                                                       prop.r 30
                                                                       prop.custom ("fill", "transparent")
                                                                       prop.strokeWidth 4
                                                                       prop.stroke "#33EE11"
                                                                       prop.custom ("strokeDasharray", 188.49)
                                                                       prop.custom ("strokeDashoffset", o) ] ] ]
                                        Html.img [ image.isRounded
                                                   prop.src playerAviPlaceholder ] ] ] ]

let private hasTimer =
    function
    | GamePhase.Waiting
    | GamePhase.Victory _ -> false
    | _ -> true

let timerComponent =
    React.functionComponent (fun (a: TimerArgs) ->
        let (progress, setProgress) = React.useState (0.)

        let subscribeToInterval () =
            let subId =
                Fable.Core.JS.setInterval (fun _ -> if hasTimer a.Phase then setProgress (progress + 1.)) 250

            { new System.IDisposable with
                member _.Dispose() = Fable.Core.JS.clearInterval (subId) }

        React.useEffect (subscribeToInterval, [| box a.Phase |])
        timerComponent' progress)
