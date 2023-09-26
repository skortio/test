

function initUserTable(tb_name, item_num, insert_pos, item_name, start)
{
        var table = document.getElementById(tb_name+"_tb");
        if (!table) {
            return
        }
        var options = []
        options.push("")
        options.push("1-id位数")
        options.push("2-vip level")
        options.push("3-level")
        options.push("4-purchase")
        options.push("5-last active hours")
        options.push("6-pkg type")

        for (var i = start; i < start + item_num; i++) {
            var row = table.insertRow(i + insert_pos - start);

            var text = row.insertCell(0);
            var item_type = row.insertCell(1);

            var s = document.createTextNode("Condition"+(i+1)+"Type");
            text.appendChild(s);

            var selectList = document.createElement("select");
            var item_cls = tb_name + "_item" + (i+1)
            selectList.setAttribute("onchange", `showItem('${item_cls}', this.selectedIndex-1)`);
            selectList.name = item_name;
            item_type.appendChild(selectList);

            for (var j = 0; j < options.length; j++) {
                var option = document.createElement("option");
                option.value = j;
                option.text = options[j];
                selectList.appendChild(option);
            }

            var item1 = row.insertCell(2);
            var item2 = row.insertCell(3);
            var item3 = row.insertCell(4);
            var item4 = row.insertCell(5);
            var item5 = row.insertCell(6);
            var item6 = row.insertCell(7);

            setLevel(1,item1, tb_name, "选择位数", i);
            setItemRange(2,item2, tb_name, "vip等级范围", i);
            setItemRange(3,item3, tb_name, "角色等级范围", i);
            setTextRange(4,item4, tb_name, "付费区间", i);
            setItemRange(5,item5, tb_name, "上次活跃时间范围小时数", i);
            setPkg(6,item6, tb_name, "包类型", i);

            showItem(item_cls, -1);
        }
}


function setItem(type, item, tb_name, text, cls_num, min, max)
{
        item.innerHTML = text + " ";
        var input = makeNumberInput(type, cls_num, min, max);
        item.className = tb_name + "_item" + (cls_num + 1);
        item.appendChild(input);
}


function setItemRange(type, item, tb_name, text, cls_num)
{
        item.innerHTML = text + " " + "minValue: ";
        var input = makeNumberInput(type, cls_num);
        item.className = tb_name + "_item" + (cls_num + 1);
        var input_m = makeNumberInput(type, cls_num);
        var logic_options = ["AND", "OR"]
        var input_h = makeSelectInput(type, logic_options, cls_num);

        item.appendChild(input);
        item.appendChild(document.createTextNode("maxValue:"));
        item.appendChild(input_m);
        item.appendChild(document.createTextNode("与下一条的关系:"));
        item.appendChild(input_h);

}

function setTextRange(type, item, tb_name, text, cls_num)
{
        item.innerHTML = text + " " + "minValue: ";
        var input = makeTextInput(type, cls_num, '0')
        item.className = tb_name + "_item" + (cls_num + 1);
        var input_m = makeTextInput(type, cls_num, '0')
        var logic_options = ["AND", "OR"]
        var input_h = makeSelectInput(type, logic_options, cls_num);

        item.appendChild(input);
        item.appendChild(document.createTextNode("maxValue:"));
        item.appendChild(input_m);
        item.appendChild(document.createTextNode("与下一条的关系:"));
        item.appendChild(input_h);

}



function makeSelectInput(index, op_param, cls_num)
{
        var selectList = document.createElement("select");
        selectList.name = "item_val_" + index + "_" + cls_num
        //Create and append the options
        //return selectList
        for (var i = 0; i < op_param.length; ++i) {
            var option = document.createElement("option");
            option.value = i;
            option.text = op_param[i];
            selectList.appendChild(option);
        }
        return selectList
}

function makeNumberInput(index, cls_num, min, max)
{
        var input = document.createElement("input");
        input.type = "number"
        input.name = "item_val_" + index + "_" + cls_num
        input.min = min
        input.max = max
        input.value = min
        return input
}

function makeTextInput(index, cls_num, default_txt, hid)
{
        var input = document.createElement("input");
        input.type = "text"
        input.name = "item_val_" + index + "_" + cls_num
        input.value = default_txt
        if (hid) {
            input.setAttribute("hidden", true)
        }
        return input
}

function showItem(cls, option)
{
        var items = document.getElementsByClassName(cls);
        var len
        for (var i = 0; i < items.length; i++) {
            len = items[i].children.length
            if (i == option) {
                items[i].removeAttribute("hidden");
                for(var k = 0; k < len; ++k){
                    items[i].children[k].removeAttribute("disabled");
                }
            }
            else {
                items[i].setAttribute("hidden", true);
                for(var k = 0; k < len; ++k){
                    items[i].children[k].setAttribute("disabled", true);
                }
            }
        }
}


function setLevel(type, item, tb_name, text, cls_num)
{
        item.innerHTML = text + " ";
        var select_options = ["个位", "十位", "百位", "千位", "万位"]
        var input = makeSelectInput(type, select_options, cls_num);
        var input_m = makeTextInput(type, cls_num, '[]')
        var logic_options = ["AND", "OR"]
        var input_h = makeSelectInput(type, logic_options, cls_num);
        item.className = tb_name + "_item" + (cls_num + 1);

        item.appendChild(input);
        item.appendChild(document.createTextNode("ID列表"));
        item.appendChild(input_m);
        item.appendChild(document.createTextNode("与下一条的关系:"));
        item.appendChild(input_h);
}


function setPkg(type, item, tb_name, text, cls_num)
{
        item.innerHTML = text + " ";
        var select_options = ["all", "ios", "android and other"]
        var input = makeSelectInput(type, select_options, cls_num);
        var input_m = makeTextInput(type, cls_num, '[]')
        var logic_options = ["AND", "OR"]
        var input_h = makeSelectInput(type, logic_options, cls_num);
        item.className = tb_name + "_item" + (cls_num + 1);

        item.appendChild(input);
        item.appendChild(document.createTextNode("包ID列表(目前为空)"));
        item.appendChild(input_m);
        item.appendChild(document.createTextNode("与下一条的关系:"));
        item.appendChild(input_h);
}