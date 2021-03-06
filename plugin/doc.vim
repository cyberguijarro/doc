if has("signs") == 0
	echohl ErrorMsg
	echo "Doc requires Vim to have +signs support."
	echohl None
	finish
endif

if has("autocmd") == 0
	echohl ErrorMsg
	echo "Doc requires Vim to have +autocmd support."
	echohl None
	finish
endif

execute ":sign define doc text=## texthl=Search"

function! DocLoad(path)
    let entries = system('python doc.py list ' . a:path)
    let lines = split(entries, '\n')
    let id = 1
    execute ":sign unplace *"

    for line in lines
        execute ":sign place " . id . " line=" . line . " name=doc buffer=" . bufnr(a:path)
        let id = id + 1
    endfor
endfunction

function! SaveBuffer()
    execute ':silent! %write !python doc.py put ' . b:doc_path . ' ' . b:doc_line
    call DocLoad(b:doc_path)
    setlocal nomodified
endfunction

function! Doc(path, line)
    let text = system('python doc.py get ' . a:path . ' ' . a:line)
    let height = winheight(0) / 4
    
    new [Documentation]
    execute ':resize ' . height
    setlocal buftype=acwrite bufhidden=wipe nobuflisted noswapfile nowrap syntax=markdown
    let b:doc_path = a:path
    let b:doc_line = a:line
    autocmd BufWriteCmd <buffer> :call SaveBuffer()
    call append(0, split(text, '\n'))
    execute 'normal ddgg' 
    setlocal nomodified
endfunction

function! DocRemove(path, line)
    call system('python doc.py remove ' . a:path . ' ' . a:line)
    call DocLoad(a:path)
endfunction

function! DocUpdate(path)
    call system('python doc.py update ' . a:path)
    call DocLoad(a:path)
endfunction

command! DocLd call DocLoad(expand("%"))
command! Doc call Doc(expand("%"), line("."))
command! DocDel call DocRemove(expand("%"), line("."))
command! DocUpd call DocUpdate(expand("%"))

augroup doc
    autocmd!
    autocmd BufWritePost * :DocUpd
    autocmd BufReadPost * :DocLd
augroup END
