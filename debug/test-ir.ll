; ModuleID = "main"
target triple = "x86_64-pc-windows-msvc"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

@"true" = constant i1 1
@"false" = constant i1 0
declare i8* @"malloc"(i32 %".1")

define i8* @"test_string"()
{
test_string_entry:
  %".2" = bitcast [7 x i8]* @"__str_0" to i8*
  ret i8* %".2"
}

@"__str_0" = global [7 x i8] c"apples\00"
define i32 @"main"()
{
main_entry:
  %".2" = call i8* @"test_string"()
  %".3" = alloca i8*
  store i8* %".2", i8** %".3"
  %".5" = load i8*, i8** %".3"
  %".6" = alloca i8*
  store i8* %".5", i8** %".6"
  %".8" = getelementptr i8*, i8** %".6", i32 0, i32 0
  %".9" = call i32 (i8*, ...) @"printf"(i8* %".8")
  ret i32 1
}
