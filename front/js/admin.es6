const customColModels = [
  {
    name: 'is_new_price',
    label: 'новая цена',
    align: 'center',
    editable: true,
    editoptions: { value: '1:0' },
    edittype: 'checkbox',
    formatter: 'checkbox',
    width: 44,
  },
  {
    name: 'in_stock',
    label: 'наличие',
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
    name: 'price',
    label: 'цена',
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
    name: 'is_popular',
    label: 'популярно',
    align: 'center',
    editable: true,
    editoptions: { value: '1:0' },
    edittype: 'checkbox',
    formatter: 'checkbox',
    width: 44,
  },
  {
    name: 'code',
    label: 'код',
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
    label: 'длина',
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
    label: 'ширина',
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
    label: 'высота',
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
    label: 'вес',
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
    label: 'объём',
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
    label: 'диаметр внешний',
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
    label: 'диаметр внутренний',
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
    label: 'марка',
    editable: true,
    width: 40,
    search: true,
  },
  {
    name: 'options_mark',
    label: 'марка',
    editable: true,
    width: 40,
    search: true,
  },
  {
    name: 'specification',
    label: 'документация',
    editable: true,
    width: 100,
  },
  {
    name: 'date_price_updated',
    label: 'дата обновления цены',
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
        defaultValue: '0.00',
      },
      date: {
        dayNames: [
          'Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat',
          'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
        ],
        monthNames: [
          'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
          'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December',
        ],
        AmPm: ['am', 'pm', 'AM', 'PM'],
        S(j) {
          return j < 11 || j > 13 ? ['st', 'nd', 'rd', 'th'][Math.min((j - 1) % 10, 3)] : 'th';
        },
        srcformat: 'Y-m-d',
        newformat: 'd/m/Y',
        parseRe: /[Tt\\\/:_;.,\t\s-]/,  // Ignore ESLintBear (no-useless-escape)
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
          YearMonth: 'F, Y',
        },
        reformatAfterEdit: false,
      },
      baseLinkUrl: '',
      showAction: '',
      target: '',
      checkbox: { disabled: true },
      idName: 'id',
    },
  },
];

const toggleFilterBtnText = {
  show: 'Показать фильтры',
  hide: 'Скрыть фильтры',
};

class STBTableEditor extends TableEditor {  // Ignore ESLintBear (no-undef)
  constructor(colModel, dialogs) {
    super(colModel, dialogs);

    this.filterFields = [
      'name',
      'mark',
      'category_name',
      'price',
    ];
  }
}

new AdminCommonPlugins();  // Ignore ESLintBear (no-undef)
new AdminSidebar();  // Ignore ESLintBear (no-undef)
const stbFilters = new TableEditorFilters(toggleFilterBtnText);  // Ignore ESLintBear (no-undef)
const stbColModel = new TableEditorColModel(customColModels, stbFilters);  // Ignore ESLintBear (no-undef)
new STBTableEditor(stbColModel);  // Ignore ESLintBear (no-undef)
