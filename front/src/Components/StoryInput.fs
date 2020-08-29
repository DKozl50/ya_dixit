module Components.StoryInput

open Feliz
open Feliz.Bulma
open Model

type private RefT = IRefValue<option<Browser.Types.HTMLInputElement>>

let private tellStory (story: RefT) =
    UserMessage.TellStory story.current.Value.value
    |> Msg.UserMsg

let private storyInputField (clickable: bool) (dispatch: Msg -> unit) (story: RefT) =
    Bulma.field.div [ field.hasAddons
                      prop.children [ Bulma.control.div [ control.isExpanded
                                                          prop.children
                                                              [ Bulma.input.text [ prop.placeholder "Ваша история тут"
                                                                                   prop.ref story ] ] ]
                                      Bulma.control.div
                                          [ Bulma.button.button [ color.isSuccess
                                                                  prop.text "Готово"
                                                                  if clickable
                                                                  then prop.onClick (fun _ ->
                                                                           tellStory story |> dispatch) ] ] ] ]

type StoryInputArgs =
    { Clickable: bool
      Dispatch: Msg -> unit }

let storyInputComponent =
    React.functionComponent (fun (a: StoryInputArgs) ->
        let ref = React.useInputRef ()
        storyInputField a.Clickable a.Dispatch ref)
