module Url

open Browser
open Model
open Util

let setURLPathname pathname =
    let url = URL.Create window.location.href
    url.pathname <- pathname
    history.pushState (obj (), null, url.toString ())

let pathnameOfState =
    function
    | ModelState.Connecting -> ""
    | ModelState.Lobby _ -> ""
    | ModelState.Room (id, _) -> "/id/" + id

let cmdUpdateURL state =
    cmdExec
    ^ fun () -> setURLPathname ^ pathnameOfState state
