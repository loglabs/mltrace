import { Position, Toaster } from "@blueprintjs/core";

export const CustomToaster = Toaster.create({
    className: "custom-toaster",
    position: Position.TOP,
    canEscapeKeyClear: true,
})