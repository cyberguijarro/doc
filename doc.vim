if has("signs") == 0
	echohl ErrorMsg
	echo "Doc requires Vim to have +signs support."
	echohl None
	finish
endif

execute ":sign define doc text=## texthl=Search"

function! DocLoad()
    let entries = system('python doc.py list ' . expand("%"))
    let lines = split(entries, '\n')
    let id = 1
    execute ":sign unplace *"

    for line in lines
        execute ":sign place " . id . " line=" . line . " name=doc buffer=" . bufnr(expand("%"))
        let id = id + 1
    endfor
endfunction

function! DocPut()
    let path = expand("%")
    let line = line(".") 
    execute '!python doc.py put ' . path . ' ' . line
    call DocLoad()
endfunction

function! DocGet()
    let text = system('python doc.py get ' . expand("%") . ' ' . line("."))
    let number = bufwinnr('^[Documentation]$')
    
    if ( number >= 0 )
        execute number . 'wincmd w'
        execute 'normal ggdG'
    else
        new [Documentation]
        setlocal buftype=nofile bufhidden=wipe nobuflisted noswapfile nowrap
    endif

    call append(0, split(text, '\n')) 
endfunction

function! DocRemove()
    execute ':silent !python doc.py remove ' . expand("%") . ' ' . line(".")
    call DocLoad()
endfunction

function! DocUpdate()
    execute ':silent !python doc.py update ' . expand("%")
    call DocLoad()
endfunction

command! DocLd call DocLoad()
command! DocPut call DocPut()
command! DocGet call DocGet()
command! DocDel call DocRemove()
command! DocUpd call DocUpdate()

autocmd FileWritePost * :DocUpd
autocmd FileReadPost * :DocLd
