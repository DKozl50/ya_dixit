module Url

open Browser
open Model
open Util

let setURLPathname pathname =
    let url = URL.Create window.location.href
    url.pathname <- pathname
    history.pushState (obj (), null, url.toString ())

let pathnameOfPage =
    function
    | Page.Connecting -> ""
    | Page.Lobby _ -> ""
    | Page.GameRoom s -> "/id/" + s.ID

let cmdUpdateURL page =
    cmdExec
    ^ fun () -> setURLPathname ^ pathnameOfPage page
