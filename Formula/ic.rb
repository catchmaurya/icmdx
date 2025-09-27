class Ic < Formula
  include Language::Python::Virtualenv
  desc "ic — intelligent command: tiny phrases → safe, powerful log/file ops"
  homepage "https://github.com/catchmaurya/icmd"
  url "https://files.pythonhosted.org/packages/source/i/icmdx/icmdx-0.1.1.tar.gz"
  sha256 "FILL_ME_AFTER_RELEASE"
  license "MIT"

  depends_on "python@3.11"
  depends_on "jq"
  depends_on "coreutils"

  def install
    virtualenv_install_with_resources
  end

  test do
    output = shell_output("#{bin}/ic 'ic: summarise --help' 2>&1", 0)
    assert_match "summarise", output
  end
end
