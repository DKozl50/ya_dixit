module Storage

open Model
open Util
open Browser.WebStorage

let loadStorage () =
    { Name = Option.ofObj localStorage.["name"]
      Avi = Option.ofObj localStorage.["avi"] }

let updateStorage (data: ClientData) =
    if data.Name.IsSome then localStorage.["name"] <- data.Name.Value
    if data.Avi.IsSome then localStorage.["avi"] <- data.Avi.Value

let updateStorageCmd data =
    cmdExec
    ^ fun _ -> updateStorage data
