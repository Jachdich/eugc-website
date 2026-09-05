
export function validate_float_string(value: string): string {
    let has_minus = value[0] == "-";
    if (has_minus) {
        value = value.substring(1);
    }
    let value_pieces = value.split(".");
    if (value_pieces.length == 1) {
        value = value_pieces[0];
    } else if (value_pieces.length == 2) {
        value = value_pieces.join(".");
    } else {
        value = value_pieces[0] + "." + value_pieces[1] + value_pieces.slice(2).join("");
    }
    value = value.replace(/[^0-9\.]/g, '');
    if (has_minus) {
        value = "-" + value;
    }

    return value;
}

