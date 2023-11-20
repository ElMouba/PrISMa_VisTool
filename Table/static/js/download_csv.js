function table_to_csv(source, number) {
    const columns = Object.keys(source.data)
    const lines = [columns.join(',')]
    for (let i = 0; i < number; i++) {
        let row = [];
        for (let j = 0; j < columns.length; j++) {
            const column = columns[j]
            row.push(source.data[column][i].toString())
        }
        lines.push(row.join(','))
    }
    return lines.join('\n').concat('\n')
}

console.log('Dowloading csv')
const number = (cb_obj)['origin']['tags'][0]
console.log((cb_obj)['origin']['tags'][1])
console.log(number)
const filename = csv_file_name + '_'+ number + '.csv'
const filetext = table_to_csv(source, number)
const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename)
} else {
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.target = '_blank'
    link.style.visibility = 'hidden'
    link.dispatchEvent(new MouseEvent('click'))
}