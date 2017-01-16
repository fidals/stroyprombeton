{
  const DOM = {
    $fileInputWrapper: $('.js-drawing-input'),
    fileInput: '.js-file-input',
  };

  const config = {
    sizeLimit: 1024 * 1024 * 20, // 20 mb
  };

  function init() {
    setUpListeners();
  }

  function setUpListeners() {
    $(DOM.fileInput).change(filesValidation);
  }

  function filesValidation(event) {
    function getFilesFromFileList(fileList) {
      const files = [];
      for (let i = 0; i < fileList.length; i += 1) {
        files.push(fileList[i]);
      }
      return files;
    }

    const fileList = $(event.target).get(0).files;
    const files = getFilesFromFileList(fileList);

    const isValidFilesCount = parseInt(fileList.length, 10) <= 10;
    const isValidFilesSize = files
      .every(file => file.size < config.sizeLimit);

    if (isValidFilesCount && isValidFilesSize) {
      DOM.$fileInputWrapper.removeClass('invalid').addClass('valid');
    } else {
      DOM.$fileInputWrapper.removeClass('valid').addClass('invalid');
    }
  }

  init();
}
