from PIL import Image
from pathlib import Path


# BAS SETTING
_LOOP_                  =   2
_HEADER_                =   r'def text asciichar { content = "" fontSize = 0.5% x = 50% y = 50% anchorX = 0.5 anchorY = 0.5 fontFamily = "Courier" color = 0xebc4e1 }'
# ASCII-PAINT SETTING
_WIDTH_                 =   160
_HEIGHT_                =   45
_CHARSET_               =   "@#&$%863!i1uazvno~;*^+-.    "
# FILE/DIR DEFINITION <= DO NOT MODIFY THIS SECTION IF YOU ARE NOVICE
_ASSETS_DIR_            =   "assets"
_CLIENT_GIF_            =   "client.gif"
_CLIENT_GIF_PATH_       =   f"{_ASSETS_DIR_}/{_CLIENT_GIF_}"
_ASCII_TXT_DIR_         =   "ascii_txt"
_BAS_OUT_DIR_           =   "bas_out"
_BAS_OUT_FILE_          =   "client.bas"
_BAS_OUT_FILE_PATH_     =   f"{_BAS_OUT_DIR_}/{_BAS_OUT_FILE_}"
_PREFRAME_DIR_          =   "gif_preframe"
_ALL_OUTPUT_DIR_LIST_   =   [_ASCII_TXT_DIR_, _BAS_OUT_DIR_, _PREFRAME_DIR_]


def clean_dir():
    if not Path(_CLIENT_GIF_PATH_).is_file():
        raise Exception(f"You ought to provide with material gif named => \
                        {_CLIENT_GIF_} at {_ASSETS_DIR_}")

    for _dir in _ALL_OUTPUT_DIR_LIST_:
        if not Path(_dir).is_dir():
            Path(_dir).mkdir(parents=True, exist_ok=True)
        else:
            for _f in Path(_dir).glob("*"):
                _f.unlink()


def charset256(charset):
    # Expand char set to 256bit
    charset_len = len(charset)
    if charset_len > 256:
        return charset[:256]
    r = 256 // charset_len
    m = 256 % charset_len
    
    s = ""
    for i in charset[:m]:
        s += i * (r + 1)
    for i in charset[m:]:
        s += i * r

    return s


def gif2multipng():
    imghandle = Image.open(_CLIENT_GIF_PATH_)
    gifstem = Path(_CLIENT_GIF_PATH_).stem
    try:
        _preframe_info_d = dict();
        while True:
            # save current frame to ../gif_preframe/client_<index>.png
            current_index = imghandle.tell()
            current_duration = imghandle.info["duration"]  # unit(int): ms
            current_png_save_path = f"{_PREFRAME_DIR_}/{gifstem}_{current_index}_{current_duration}.png"
            imghandle.save(current_png_save_path)
            # Get next frame
            imghandle.seek(current_index+1)
            _preframe_info_d[current_index] = {"filepath": current_png_save_path, "duration": current_duration}
    except EOFError:
        pass

    return _preframe_info_d


def image2char(image, width, height, charset):
    # convert png to ascii-char
    # convert to grey mode
    image = image.convert("L").resize((width, height))
    pix = image.load()

    char_l = []
    for i in range(height):
        for j in range(width):
            # read pixel and map to char
            char = charset[pix[j, i]]
            char_l.append(char)
        char_l.append("\n")
    # return ascii-char
    return "".join(char_l)


def png2ascii_batch(_preframe_info_d: dict):
    _asciichar_info_d = dict()
    for index, info_d in _preframe_info_d.items():
        pngfile = info_d["filepath"]
        pngfile_stem = Path(info_d["filepath"]).stem
        postfix = pngfile_stem.split("_")[0]
        current_ascii_save_path = f"{_ASCII_TXT_DIR_}/{postfix}_ascii_{index}.txt"
        current_char_l = image2char(Image.open(pngfile), _WIDTH_, _HEIGHT_, charset256(_CHARSET_))
        with open(current_ascii_save_path, "w+") as f_wi:
            f_wi.write(current_char_l)
        _asciichar_info_d[index] = {"filepath": current_ascii_save_path, "duration": info_d["duration"]}
    
    return _asciichar_info_d


def ascii2bas_batch(_asciichar_info_d: dict):
    cmd_prefix = 'then '
    flag_first_line = True
    with open(_BAS_OUT_FILE_PATH_, 'w+') as f_bas:
        f_bas.write(_HEADER_)  # already with newline char "\n"
        f_bas.write('\n')
        for _ in range(_LOOP_):
            for index, info_d in _asciichar_info_d.items():
                duration = int(info_d["duration"])/1000
                asciifile = info_d["filepath"]
                with open(asciifile, 'r') as f_ascii:
                    _content = f_ascii.read().replace('\n', '\\n')
                    cmd_prefix = '' if flag_first_line else 'then '
                    if flag_first_line: flag_first_line = not flag_first_line
                    bas_cmd = cmd_prefix + 'set asciichar { content = "' + _content + '" } ' + str(duration) + 's \n'
                    f_bas.write(bas_cmd)


if __name__ == "__main__":
    clean_dir()
    preframe_info_d = gif2multipng()
    asciichar_info_d = png2ascii_batch(preframe_info_d)
    ascii2bas_batch(asciichar_info_d)
    print(f'[SUCCESS] BAS File Generated DONE : \n\t{_BAS_OUT_FILE_PATH_}\n')
