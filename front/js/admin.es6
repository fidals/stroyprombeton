const customColumnModels = [
  {
    name: 'is_new_price',
    label: 'Is new price',
    align: 'center',
    editable: true,
    editoptions: { value: '1:0' },
    edittype: 'checkbox',
    formatter: 'checkbox',
    width: 44,
  },
  {
    name: 'code',
    label: 'Code',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1',
      min: '0',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 0,
      number: true,
    },
    sorttype: 'integer',
    width: 50,
  },
  {
    name: 'length',
    label: 'Length',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1',
      min: '0',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 0,
      number: true,
    },
    sorttype: 'integer',
    width: 50,
  },
  {
    name: 'width',
    label: 'Width',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1',
      min: '0',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 0,
      number: true,
    },
    sorttype: 'integer',
    width: 50,
  },
  {
    name: 'height',
    label: 'Height',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1',
      min: '0',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 0,
      number: true,
    },
    sorttype: 'integer',
    width: 50,
  },
  {
    name: 'weight',
    label: 'Weight',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1.00',
      min: '0.00',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 0,
      number: true,
    },
    sorttype: 'integer',
    width: 50,
  },
  {
    name: 'volume',
    label: 'Volume',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1.00',
      min: '0.00',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 0,
      number: true,
    },
    sorttype: 'integer',
    width: 50,
  },
  {
    name: 'diameter_out',
    label: 'Diameter out',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1',
      min: '0',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 0,
      number: true,
    },
    sorttype: 'integer',
    width: 50,
  },
  {
    name: 'diameter_in',
    label: 'Diameter in',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1',
      min: '0',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 0,
      number: true,
    },
    sorttype: 'integer',
    width: 50,
  },
  {
    name: 'mark',
    label: 'Mark',
    editable: true,
    width: 80,
  },
  {
    name: 'specification',
    label: 'Specification',
    editable: true,
    width: 100,
  },
  {
    name: 'date_price_updated',
    label: 'Date price updated',
    editable: true,
    width: 100,
    formatter: {
      integer: {
        thousandsSeparator: '',
        defaultValue: '0',
      },
      number: {
        decimalSeparator: '.',
        thousandsSeparator: '',
        decimalPlaces: 2,
        defaultValue: '0.00',
      },
      currency: {
        decimalSeparator: '.',
        thousandsSeparator: '',
        decimalPlaces: 2,
        prefix: '',
        suffix: '',
        defaultValue: '0.00'
      },
      date: {
        dayNames: [
          'Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat',
          'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
        ],
        monthNames: [
          'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
          'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'
        ],
        AmPm : ['am','pm','AM','PM'],
        S: function (j) {return j < 11 || j > 13 ? ['st', 'nd', 'rd', 'th'][Math.min((j - 1) % 10, 3)] : 'th'},
        srcformat: 'Y-m-d',
        newformat: 'd/m/Y',
        parseRe: /[Tt\\\/:_;.,\t\s-]/,
        masks: {
          ISO8601Long: 'Y-m-d H:i:s',
          ISO8601Short: 'Y-m-d',
          ShortDate: 'n/j/Y',
          LongDate: 'l, F d, Y',
          FullDateTime: 'l, F d, Y g:i:s A',
          MonthDay: 'F d',
          ShortTime: 'g:i A',
          LongTime: 'g:i:s A',
          SortableDateTime: 'Y-m-d\\TH:i:s',
          UniversalSortableDateTime: 'Y-m-d H:i:sO',
          YearMonth: 'F, Y'
        },
        reformatAfterEdit : false
      },
      baseLinkUrl: '',
      showAction: '',
      target: '',
      checkbox : {disabled:true},
      idName : 'id'
    }
  },
];

class TableEditorSE extends TableEditor {
  constructor(colModel = new TableEditorColumnModel(), dialogBoxes = new TableEditorDialogBoxes()) {
    super(colModel, dialogBoxes);

    this.filterFields = [
      'name',
      'category_name',
      'price',
    ];
  }
}

new AdminSideBar();
new AdminCommonPlugins();
const tableEditorDialogBoxes = new TableEditorDialogBoxes();
const tableEditorFilters = new TableEditorFilters();
const tableEditorColumnModel = new TableEditorColumnModel(tableEditorFilters, customColumnModels);
new TableEditorSE(tableEditorColumnModel, tableEditorDialogBoxes);
