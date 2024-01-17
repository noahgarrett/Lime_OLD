; ModuleID = "main"
target triple = "x86_64-pc-windows-msvc"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

@"true" = constant i1 1
@"false" = constant i1 0
declare i8* @"malloc"(i32 %".1")

define [1 x i8] @"test_str"()
{
test_str_entry:
  ret [7 x i8] c"Apples\00"
}

define i32 @"main"()
{
main_entry:
  %".2" = call [1 x i8] @"test_str"()
  %".3" = alloca [1 x i8]
  store [1 x i8] %".2", [1 x i8]* %".3"
  %".5" = alloca [4 x i8]
  store [4 x i8] c"yes\00", [4 x i8]* %".5"
  %".7" = alloca [5 x i8]
  store [5 x i8] c"test\00", [5 x i8]* %".7"
  %".9" = getelementptr [5 x i8], [5 x i8]* %".7", i32 0, i32 0
  %".10" = call i32 (i8*, ...) @"printf"(i8* %".9")
  ret i32 0
}
