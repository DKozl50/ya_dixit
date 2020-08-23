module Components.Table

open Feliz
open Feliz.Bulma
open Feliz.Bulma.Operators
open Model

type TableArgs =
    { Cards: ReactElement list }

let tableComponent =
    React.functionComponent (fun (a: TableArgs) -> a.Cards)

