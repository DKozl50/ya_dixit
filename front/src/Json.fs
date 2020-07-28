module Json

open Model
open Monad
open Thoth.Json

let inline invalid<'T> x = System.String.Format("{} is not a valid {}", x, nameof typeof<'T>)

type PlayerSide with
    static member OfString = function
        | "Cross" -> Ok PlayerSide.Cross
        | "Nought" -> Ok PlayerSide.Nought
        | s -> DecoderError(s, FailMessage (invalid<PlayerSide> s)) |> Error
       
    static member Decoder : Decoder<PlayerSide> = 
        fun s x -> Decode.string s x >>= PlayerSide.OfString

    static member Encoder : Encoder<PlayerSide> = 
        fun x -> x.ToString() |> Encode.string
