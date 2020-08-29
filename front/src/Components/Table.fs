module Components.Table

open Feliz
type TableArgs =
    { Cards: ReactElement list }

let tableComponent =
    React.functionComponent (fun (a: TableArgs) -> a.Cards)

