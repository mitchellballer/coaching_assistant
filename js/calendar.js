today = new Date();
currentMonth = today.getMonth();
currentYear = today.getFullYear();

showCalendar(currentMonth, currentYear);

function showCalendar(month, year){
    let firstDay = (new Date(year, month)).getDay();

    tbl = document.getElementById("calendar_body");

    //clear any existing cells/content
    tbl.innerHTML = "";

    let date = 1;
    for (let i = 0; i < 6; i++){
        //create a table row
        let row = document.createElement("tr");

        //create cells, populate
        for (let j = 0; j < 7; j++){
            if (i == 0 && j<firstDay){
                cell = document.createElement("td");
                cellText = document.createTextNode("");
                cell.appendChild(cellText);
                row.appendChild(cell);
            }
            else if (date > daysInMonth(month, year)) {
                break;
            }
            else {
                cell = document.createElement("td");
                cellText = document.createTextNode(date);
                cell.appendChild(cellText);
                row.appendChild(cell);
                date++;
            }
        }

        tbl.appendChild(row);
    }
}

// check how many days in a month code from https://dzone.com/articles/determining-number-days-month
function daysInMonth(iMonth, iYear) {
    return 32 - new Date(iYear, iMonth, 32).getDate();
}