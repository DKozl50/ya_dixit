module Components.Story

open Feliz
open Feliz.Bulma
open Model

type StoryComponentArgs =
    { Player: Player
      Story: string option }

let private msgOfStoryO =
    function
    | None -> "Is making up a story"
    | Some s -> sprintf "Tells a story: %s" s

let private storyComponent' (a: StoryComponentArgs) =
    Bulma.levelItem [ spacing.ml5
                      prop.children
                          [ Bulma.container [ Bulma.title.h3 [ title.is3
                                                               prop.text (a.Player.Name) ]
                                              Html.p (msgOfStoryO a.Story) ] ] ]

let storyComponent = React.functionComponent storyComponent'
