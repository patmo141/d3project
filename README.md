# cookie_cutter_examples

This project is a collection of minimal examples of how to build rich interactive addon user interfaces using the CGCookie addon_common library.

# Tutorials

This project will follow along with some youtube videos


# How to Set Up

I have setup addon_common as a "subtree" of this repository, the main purpose of which is to allow github projects which leverage this to pull down the addon_common directory in the .zip.  Subtrees allow for relatively easy tracking and pushing of code to subtree repositories.   For projects that use addon_common as a subtree you can set it up like this

```
git remote add addon_common https://github.com/CGCookie/addon_common.git
git subtree add --prefix=subtrees/addon_common addon_common b280
```

this sets up the addon_common repository in a directory called "subtrees"  in your project.
later when you want to pull updates from addon_common

```
git subtree pull —prefix=subtrees/addon_common addon_common b280
```

If your project is using addon_common master branch, replace "b280" with "master"
