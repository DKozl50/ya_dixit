module Tests

open Fable.Mocha

let appTests = testList "App tests" []

let allTests = testList "All" [
    appTests
]

[<EntryPoint>]
let main (args: string[]) = Mocha.runTests allTests
