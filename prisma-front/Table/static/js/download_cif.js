const content_cif = (cb_obj)['origin']['tags'][0]
const filename_cif = (cb_obj)['origin']['tags'][1]

console.log('Dowloading cif')
console.log(filename_cif)

var blob = new Blob([content_cif], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename_cif);
} else {
    
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename_cif
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}