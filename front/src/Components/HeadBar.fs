module Components.HeadBar

open Feliz
open Feliz.Bulma
open Model

open Components.Story
open Components.StoryInput
open Components.Timer

type HeadBarArgs =
    { Phase: GamePhase
      Storyteller: Player
      ActiveInput: bool
      ActiveButton: bool
      Story: string option
      Dispatch: Msg -> unit }


let private headBarComponent' (a: HeadBarArgs) =
    Bulma.card [ prop.className "top"
                 prop.children
                     [ Bulma.cardContent [ Bulma.level [ timerComponent
                                                             { Phase = a.Phase
                                                               Player = a.Storyteller }
                                                         storyComponent
                                                             { Story = a.Story
                                                               Player = a.Storyteller }
                                                         Bulma.levelRight [] ]
                                           if a.ActiveInput then
                                               storyInputComponent
                                                   { Clickable = a.ActiveButton
                                                     Dispatch = a.Dispatch } ] ] ]

let headBarComponent =
    React.functionComponent headBarComponent'